"""
@file cli.py
@brief ctk command-line tool for managing and analyzing chat logs.

This script provides subcommands to import, list, merge, run jmespath queries,
launch a Streamlit dashboard, etc. It uses doxygen-style tags for documentation.
"""

import argparse
import json
import os
import sys
import AlgoTree
import subprocess
from rich.console import Console
from rich.json import JSON
from  .utils import ( load_conversations, save_conversations, pretty_print_conversation, 
                    query_conversations_search, query_conversations_jmespath, path_value,
                    list_conversations, ensure_libdir_structure, print_json_as_table)
from .merge import union_libs, intersect_libs, diff_libs


from .llm import query_llm
from .vis import generate_url_graph, visualize_graph_pyvis, visualize_graph_png, display_graph_stats
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

def launch_streamlit_dashboard(libdir):
    """
    @brief Launch a Streamlit-based dashboard for exploring the ctx lib.
    @param libdir Path to the conversation library directory.
    @return None
    @details This function just outlines how you'd call Streamlit. 
    """
    dash_cmd = [
        "streamlit", "run",
        "streamlit/app.py",
        #"--",  # pass CLI arguments to the Streamlit app
        f"--libdir={libdir}"
    ]
    subprocess.run(dash_cmd, check=True)


################################################################################
# COMMAND-LINE INTERFACE (argparse)
################################################################################

def main():
    """
    @brief Main entry point for the ctk CLI.
    @return None
    """
    parser = argparse.ArgumentParser(
        description="ctk: A command-line tool for chat log management and analysis."
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # Subcommand: search
    regex_parser = subparsers.add_parser("search", help="Run a search using regex against the ctk lib on the specified fields")
    regex_parser.add_argument("libdir", help="Path to the conversation library directory")
    regex_parser.add_argument("expression", help="Regex expression")
    regex_parser.add_argument("--fields", nargs="+", help="Field paths to apply the regex", default=["title"])
    regex_parser.add_argument("--json", action="store_true", help="Output as JSON. Default: False")

    # Subcommand: conversation-tree
    tree_parser = subparsers.add_parser("conv-stats", help="Compute conversation tree statistics")
    tree_parser.add_argument("libdir", help="Path to the conversation library directory")
    tree_parser.add_argument("index", type=int, help="Index of conversation tree")
    tree_parser.add_argument("--json", action="store_true", help="Output as JSON. Default: False")
    tree_parser.add_argument("--no-payload", action="store_true", help="Do not show payload in the output. Default: False")

    # Subcommand: show-conversation-tree
    show_tree_parser = subparsers.add_parser("tree", help="Conversation tree visualization")
    show_tree_parser.add_argument("libdir", help="Path to the conversation library directory")
    show_tree_parser.add_argument("index", type=int, help="Index of conversation tree to visualize")
    show_tree_parser.add_argument("--label-fields", nargs="+", 
                                  type=str, default=['id', 'message.content.parts'], help="When showing the tree, use this field as the node's label")
    show_tree_parser.add_argument("--truncate", type=int, default=8, help="Truncate each field to this length. Default: 8")

    # Subcommand: conversation
    conv_parser = subparsers.add_parser("conv", help="Print conversation based on a particular node id. Defaults to using `current_node` for the corresponding conversation tree.")
    conv_parser.add_argument("libdir", help="Path to the conversation library directory")
    conv_parser.add_argument("indices", nargs="+", type=int, help="Indices of conversations to print")
    conv_parser.add_argument("--node", default=None, help="Node id that indicates the terminal node of a conversation path")
    conv_parser.add_argument("--json", action="store_true", help="Output as JSON")
    conv_parser.add_argument("--msg-limit", type=int, default=1000, help="Limit the number of messages to display. Default: 1000")
    conv_parser.add_argument("--msg-roles", type=str, nargs="+", default=["user", "assistant"], help="Roles to include in message output")
    conv_parser.add_argument("--msg-start-index", type=int, default=0, help="Start index for messages to display. Default: 0")
    conv_parser.add_argument("--msg-end-index", type=int, default=-1, help="End index for messages to display. Default: -1 (end of list). Use negative values to count from the end.")

    # Subcommand: remove
    remove_parser = subparsers.add_parser("remove", help="Remove a conversation from the ctk lib")
    remove_parser.add_argument("libdir", help="Path to the conversation library directory")
    remove_parser.add_argument("indices", type=int, nargs="+", help="Indices of conversations to remove")

    # Subcommand: share
    share_parser = subparsers.add_parser("export", help="Export a conversation from the ctk lib")
    share_parser.add_argument("libdir", help="Path to the conversation library directory")
    share_parser.add_argument("indices", type=int, nargs="+", default=None, help="Indices of conversations to export. Default: all")
    share_parser.add_argument("--format", choices=["json", "markdown", "hugo", "zip"], default="json", help="Output format")

    # Subcommand: list
    list_parser = subparsers.add_parser("list", help="List all conversations in the ctk lib")
    list_parser.add_argument("libdir", help="Path to the conversation library directory")
    list_parser.add_argument("--indices", nargs="+", default=None, type=int, help="Indices of conversations to list. Default: all")
    list_parser.add_argument("--fields", nargs="+", default=["title", "update_time"], help="Path fields to include in the output")

    # Subcommand: merge (union, intersection, difference)
    merge_parser = subparsers.add_parser("merge", help="Merge multiple ctk libs into one")
    merge_parser.add_argument("operation", choices=["union", "intersection", "difference"],
                              help="Type of merge operation")
    merge_parser.add_argument("libdirs", nargs="+", help="List of library directories")
    merge_parser.add_argument("-o", "--output", required=True, help="Output library directory")

    # Subcommand: jmespath
    jmespath_parser = subparsers.add_parser("jmespath", help="Run a JMESPath query on the ctk lib")
    jmespath_parser.add_argument("libdir", help="Path to the conversation library directory")
    jmespath_parser.add_argument("query", help="JMESPath expression")

    # Subcommand: dash
    dash_parser = subparsers.add_parser("dash", help="Launch Streamlit dashboard")
    dash_parser.add_argument("libdir", help="Path to the conversation library directory")

    # Subcommand: llm
    llm_parser = subparsers.add_parser('llm', help='Query the ctk library using a Large Language Model for natural language processing')
    llm_parser.add_argument('lib_dir', type=str, help='Directory of the ctk library to query')
    llm_parser.add_argument('query', type=str, help='Query string')
    llm_parser.add_argument('--json', action='store_true', help='Output in JSON format')

    # Subcommand: viz
    viz_parser = subparsers.add_parser('viz', help='Visualize the conversation library as a complex network')
    viz_parser.add_argument('libdir', type=str, help='Directory of the ctk library to visualize')
    viz_parser.add_argument('output_format', type=str, help='Output format: html, png, json')
    viz_parser.add_argument('--limit', type=int, default=5000, help='Limit the number of conversations to visualize')

    # Subcommand: purge
    purge_parser = subparsers.add_parser('purge', help='Purge dead links from the conversation library')
    purge_parser.add_argument('libdir', type=str, help='Directory of the ctk library to purge')

    # Subcommand: visit
    visit_parser = subparsers.add_parser('web', help='View a conversation in the OpenAI chat interface')
    visit_parser.add_argument('libdir', type=str, help='Directory of the ctk library to visit')
    visit_parser.add_argument('index', type=int, nargs='+', help='Indices of the conversations to view in the browser')

    # Subcommand: version
    version_parser = subparsers.add_parser('version', help='Print the version of ctk')

    # Subcommand: about
    about_parser = subparsers.add_parser('about', help='Print information about ctk')

    args = parser.parse_args()

    if args.command == "list":
        list_conversations(args.libdir, args.fields, args.indices) 

    elif args.command == "search":
        results = query_conversations_search(args.libdir, args.expression, args.fields)
        if args.json:
            # pretty JSON
            console.print(JSON(json.dumps(results, indent=2)))
        else:
            for conv in results:
                pretty_print_conversation(conv)

    elif args.command == "remove":
        conversations = load_conversations(args.libdir)
        for index in sorted(args.indices, reverse=True):
            del conversations[index]
        save_conversations(args.libdir, conversations)
        logger.debug(f"Removed {len(args.indices)} conversations")

    elif args.command == "export":
        print("TODO: Implement export command")

    elif args.command == "version":
        # grab version from the pypi package
        from . import version

        console.print(f"ctk version {version}")

    elif args.command == 'llm':
        lib_dir = args.lib_dir
        if not os.path.isdir(lib_dir):
            logging.error(f"The specified library directory '{lib_dir}' does not exist or is not a directory.")
            sys.exit(1)
        conversations = load_conversations(lib_dir)

        while True:
            try:
                results = query_llm(lib_dir, args.query)
                results = json.loads(results['response'])

                cmd = results["command"]
                arglist = results["args"]
                proc = ["ctk"] + [cmd] + arglist
                console.print(f"[bold green]Executing:[/bold green] {' '.join(proc)}")  
                subprocess.run(proc, check=True)
                break
            # catch any exceptions and continue
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                continue

    elif args.command == "jmespath":
        result = query_conversations_jmespath(args.libdir, args.query)
        # pretty print
        console.print(JSON(json.dumps(result, indent=2)))


    elif args.command == "conv-stats":
        conversations = load_conversations(args.libdir)
        if args.index >= len(conversations):
            console.debug(f"[red]Error: Index {index} out of range.[/red]")
        conv = conversations[args.index]

        cur_node_name = conv.get("current_node")
        
        tree_map = conv.get("mapping")
        t = AlgoTree.FlatForest(tree_map)
        cur_node = t.node(cur_node_name)
        ancestors = AlgoTree.utils.ancestors(cur_node)
        cur_conv_ids = [node.name for node in ancestors] + [cur_node_name]

        stats = {}
        metadata = conv
        metadata.pop("mapping", None)

        stats['metadata'] = metadata
        stats["num_paths"] = len(AlgoTree.utils.leaves(t.root))
        stats["num_nodes"] = AlgoTree.utils.size(t.root)
        stats["max_path"] = AlgoTree.utils.height(t.root)

        def walk(node):
            node_dict = {}
            siblings = AlgoTree.utils.siblings(node)
            node_dict["num_siblings"] = len(siblings)
            node_dict["is_leaf"] = AlgoTree.utils.is_leaf(node)
            node_dict["is_root"] = AlgoTree.utils.is_root(node)
            node_dict["is_current"] = node.name in cur_conv_ids
            node_dict["num_children"] = len(node.children)
            node_dict["depth"] = AlgoTree.utils.depth(node)
            node_dict["num_descendants"] = AlgoTree.utils.size(node)
            node_dict["num_ancestors"] = len(AlgoTree.utils.ancestors(node))
            if not args.no_payload:
               node_dict['payload'] = node.payload
            
            # let id be the enumaration of the nodes
            id = len(stats)
            stats[id] = node_dict

            for child in node.children:
                walk(child)

        walk(t.root)
        if args.json:
            console.print(JSON(json.dumps(stats, indent=2)))
        else:
            print_json_as_table(stats, table_title=conv['title'])

    elif args.command == "tree":
        convs = load_conversations(args.libdir)
        if args.index >= len(convs):
            console.debug(f"[red]Error: Index {index} out of range.[/red]")
            sys.exit(1)
        conv = convs[args.index]
        tree_map = conv.get("mapping", {})
        t = AlgoTree.FlatForest(tree_map)

        paths = []
        for field in args.label_fields:
            paths.append(field.split('.'))

        def get_label(node):
            results = []
            for path in paths:
                value = path_value(node.payload, path)
                value = value[:args.truncate]
                results.append(value)

            label = " ".join(results)
            return label\

        console.print(AlgoTree.pretty_tree(t, node_name=get_label))

    elif args.command == "purge":
        print("TODO: Implement purge command. This swill remove any local files that are dead links in the library.")

    elif args.command == "conv":

        if args.node is not None and len(args.indices) >1:
            console.print("[red]Error: If you specify a node, you can only print one conversation at a time.[/red]")
            sys.exit(1)

        convs = load_conversations(args.libdir)
        json_obj = []

        for idx in args.indices:                
            if idx >= len(convs):
                console.debug(f"[red]Error: Index {idx} in indices out of range.[/red]. Skipping.")
                continue

            if args.json:
                json_obj.append(convs[idx])
            else:
                pretty_print_conversation(
                    convs[idx],
                    terminal_node = args.node,
                    msg_limit = args.msg_limit,
                    msg_roles = args.msg_roles,
                    msg_start_index = args.msg_start_index,
                    msg_end_index = args.msg_end_index)

        if args.json:
            console.print(JSON(json.dumps(json_obj, indent=2)))

    elif args.command == "about":
        console.print("[bold cyan]ctk[/bold cyan]: A command-line toolkit for working with conversation trees, "
                    "typically derived from exported LLM interaction data.\n")
        console.print("[bold]Version:[/bold] 0.1.0")
        console.print("[dim]Developed by:[/dim] [bold white]Alex Towell[/bold white]  \n"
                    "[dim]Contact:[/dim] [link=mailto:lex@metafunctor.com]lex@metafunctor.com[/link]  \n"
                    "[dim]Source Code:[/dim] [link=https://github.com/queelius/ctk]https://github.com/queelius/ctk[/link]\n")
        console.print("[bold]Features:[/bold]")
        console.print("• Parse and analyze LLM conversation trees.")
        console.print("• Export, transform, and query structured conversation data.")
        console.print("• Visualize conversation trees and relationships.")
        console.print("• Query conversation trees using JMESPath.")
        console.print("• Query conversation trees using an LLM.")
        console.print("• Launch a Streamlit dashboard for interactive exploration.")
        console.print("• Lightweight and designed for command-line efficiency.")
        console.print("\n[bold green]Usage:[/bold green] Run `ctk --help` for available commands.")


    elif args.command == "web":
        convs = load_conversations(args.libdir)
        
        import webbrowser

        for idx in args.index:
            if idx < 0 or idx >= len(convs):
                console.debug(f"[red]Error: Index {idx} out of range.[/red]. Skipping.")
                continue
        
            conv = convs[idx]
            link = f"https://chat.openai.com/c/{conv['id']}"
            webbrowser.open_new_tab(link)

    elif args.command == "merge":
        ensure_libdir_structure(args.output)
        if args.operation == "union":
            union_libs(args.libdirs, args.output)
            logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")
        elif args.operation == "intersection":
            intersect_libs(args.libdirs, args.output)
            logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")
        elif args.operation == "difference":
            diff_libs(args.libdirs, args.output)
            logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")
        logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")

    elif args.command == "dash":
        launch_streamlit_dashboard(args.libdir)

    elif args.command == "viz":
        convs = load_conversations(args.libdir)
        net = generate_url_graph(convs, args.limit)
        if args.output_format == 'png':
            visualize_graph_png(net, 'graph.png')
        elif args.output_format == 'html':
            visualize_graph_pyvis(net, 'graph.html')
        elif args.output_format == 'json':
            display_graph_stats(net)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
